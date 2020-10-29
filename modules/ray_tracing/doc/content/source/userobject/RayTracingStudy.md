# RayTracingStudy

The `RayTracingStudy` is the base object for generating and tracing of [Rays](Ray.md) with the [Ray Tracing Module](ray_tracing/index.md). For information about the manipulation of [Rays](Ray.md) once they have began tracing, see [RayKernels/index.md] and [RayBCs/index.md].

!alert tip
The majority of the information presented here is for +advanced+ used only. The use of this module for simple cases like line sources (see [line_sources.md]) and line integrals (see [line_integrals.md]) utilize the [RepeatableRayStudy.md]. Please see [RepeatableRayStudy.md] first for a more general understanding. If the [RepeatableRayStudy.md] is not sufficient for your use case, please then reference the [RepeatableRayStudyBase.md] instead.

## Execution Phases

The execution of the  `RayTracingStudy` is split up into two phases:

- [#generation] - The [Rays](Ray.md) to be traced are defined and moved into the buffer to be traced
- [#propagation] - The [Rays](Ray.md) are traced until completion

### Generation

To use the `RayTracingStudy`, you are to derive from it and override the `generateRays()` method. Within `generateRays()`, you are to create [Rays](Ray.md), set their trajectories (for more information, see [Ray.md#defining-a-ray-trajectory]), set their data (if any, see [Ray.md#using-ray-data] for more information), and move them into the buffer to be traced with `moveRayToBuffer()` or `moveRaysToBuffer()`.

If you know in advance the number of [Rays](Ray.md) that you are adding to the buffer to be traced during generation, it is advised call `reserveRayBuffer()` with the number of [Rays](Ray.md) to be moved to the buffer +before+ moving them into the buffer.

### Propagation

The Ray propagation phase traces the [Rays](Ray.md) that were added to the buffer to be traced. This is done internally by the `propagatateRays()` method. Note that additional [Rays](Ray.md) may be added to be traced during the propagation phase via [RayKernels/index.md] and [RayBCs/index.md]. For more information, see [RayKernels/index.md#creating-additional-rays] for creating [Rays](Ray.md) within [RayKernels/index.md] and [RayBCs/index.md#creating-a-new-ray] for creating [Rays](Ray.md) within [RayBCs/index.md].

## Specialization

There are many methods that can be overridden in your derived class. A summary of such methods follows:

- `generateRays()` - +MUST+ override to define and move the [Rays](Ray.md) into the buffer to be traced (see [#generation])
- `preExecuteStudy()` - Called before [#generation]
- `postExecuteStudy()` - Called after [#propagation]
- `postOnSegment()` - Called after each segment of a [Ray.md]
- `onCompleteRay()` - Called when the trace of a [Ray.md] has ended
- `buildSegmentQuadrature()` Called to generate the 1D quadrature across a [Ray.md] segment

## Helper Systems

The `RayTracingStudy` contains many systems that aid in the generation and manipulation of [Rays](Ray.md):

- [Ray Data Registration](#ray-data-registration): Registers indicies into data and auxiliary data to be stored on each [Ray.md]
- [Ray Registration](#ray-registration): Registers names to be associated with each [Ray.md] and requires [RayBCs/index.md] and [RayKernels/index.md] to provide which [Rays](Ray.md) they are applied to
- [Ray Banking](#ray-banking): Banks [Rays](Ray.md) once they end to be accessed after tracing
- [Ray Pool](#ray-pool): A shared pool of [Rays](Ray.md) that allows for their reuse after they are called to be destructed
- [Unique Ray IDs](#unique-ray-ids): Generates a unique ID across processors and threads for a [Ray.md]
- [Side Normal Caching](#side-normal-caching): Generates and caches (for future use) outward normals for an element

### Ray Data Registration

The data and auxiliary data associated with a [Ray.md] is stored on the [Ray.md] itself in the form of two `std::vector<RayData>` (`RayData` is typically a `Real`), which are accessed via `Ray::data()` and `Ray::auxData()`. A data registration system exists that allows for the study, [RayKernels/index.md], and [RayBCs/index.md] to request the data and auxiliary data that they need upon construction.

To register value(s), use the methods `registerRayData()` and `registerRayAuxData()`, which return either a single index or a vector of indices into the `Ray::data()` and `Ray::auxData()` vectors that you should utilize. If the same value is registered (uses the same name) within multiple objects, the same index will be returned.

The `Ray::data()` and `Ray::auxData()` sizes are set automatically under the hood to the registered sizes in some derived studies, but in general for more advanced used cases you should always size the data on each [Ray.md] before it is added to the buffer to be traced. More so if you are modifying the data before a trace - you will likely need to resize the vectors on the [Ray.md] first. The data should be sized using the `rayDataSize()` and `rayAuxDataSize()` methods found in the study. These methods will return the current size of data and auxiliary data registered.

### Ray Registration

For cases in which only a few [Rays](Ray.md) are generated, it is beneficial to have a registration system that allows for the user to access a specific [Ray](Ray.md) by name instead of an ID. Specific examples are line sources (see [line_sources.md]) and line integrals (see [line_integrals.md]), which utilize the [RepeatableRayStudy.md].

The enabling and disabling of ray registration is handled by the `_use_ray_registration` private parameter, for which the default is true. When ray registration is enabled, all [RayKernels/index.md] and [RayBCs/index.md] +must+ have the parameter [!param](/RayKernels/NullRayKernel/rays) set, which identifies the [Rays](Ray.md) by name that said objects are executed on. When ray registration is disabled, the [!param](/RayKernels/NullRayKernel/rays) parameter cannot be used and [RayKernels/index.md] and [RayBCs/index.md] will be executed for +all+ [Rays](Ray.md).

Use the protected methods `registerRay()` and `registerRays()` for the registration of [Ray(s)](Ray.md) with the given name(s). These methods will return the ID(s) that are to be assigned to the [Ray(s)](Ray.md). In order to use ray registration, the registration methods must be called on all processors at the same time.

The public methods `registeredRayID()` and `registeredRayName()` can be utilized to map a registered [Ray.md] name to its ID and an ID to its registered name, respectively.

### Ray Banking

It is often useful to examine a [Ray.md] after is has completed tracing. An example use case is for obtaining the accumulated integral for a [Ray.md] that is integrating a field along a line (see [line_integrals.md] and [IntegralRayKernel.md]). Within line integrals, the [Ray.md] banks will be accessed to obtain the final accumulated value in a [Ray.md].

With the `_bank_rays_on_completion` private parameter set to true, all [Rays](Ray.md) that complete on a given processor are stored in the private member variable `_ray_bank`. This bank can be accessed through the `rayBank()` method or via `getBankedRay()`, which will return the [Ray.md] with the requested ID on the processor that ended the [Ray.md].

In addition, the methods `getBankedRayData()` and `getBankedRayAuxData()` are available to get a single data value from a [Ray.md] from the banks after it has completed. For these methods, the resulting value is replicated across all processors.

### Ray Pool

For simulations with the [ray_tracing/index.md] that generate of a large number of [Ray.md] objects, it becomes advantageous to minimize the construction of new [Ray.md] objects. More so whenever the size of the data on the [Ray.md] is significant.

[Ray.md] storage is typically wrapped as a `std::shared_ptr<Ray>`. The significance of using a `shared_ptr` is that the destructor is called when the use count reaches zero, that is, when nobody is holding onto the [Ray.md]. The internal tracing algorithm will decrease the use count for a traced [Ray.md] after it has completed tracing. That is, if no other shared ownership of the [Ray.md] exists, the use count will reach zero. This is why [#ray-banking] exists - the [Ray.md] bank will increase the use count of the [Ray.md] so that it is available for use after tracing and is not destructed.

Within the [Ray.md] object, for every constructor there exists a `reset()` method with the same arguments. The purpose being that if you construct a new [Ray.md] or call `reset()` on a current [Ray.md] with the same arguments, the resulting [Ray.md] will be the same. This allows for the re-use of an older [Ray.md] object without allocating new memory.

The study holds a shared pool of [Ray.md] objects. Any [Rays](Ray.md) that were acquired from the pool will be returned to the pool once their use count reaches zero to be available for future use when acquiring another [Ray.md] from the pool. To acquire a [Ray.md] from the pool, use the method `acquireRay()`, for which the first argument is the thread ID and the remaining arguments are the arguments to be passed to the [Ray.md] constructor or `reset()` method.

In summary, you should +always+ obtain a [Ray.md] from the pool using the `acquireRay()` method. This allows for the re-use of previously allocated [Rays](Ray.md) that have had their use counts hit zero.

There exist specialized `acquireRay()` methods within [RayKernels/index.md] and [RayBCs/index.md] for the purpose of creating a [Ray.md] while tracing. For more information, see [RayKernels/index.md#creating-additional-rays] for creating [Rays](Ray.md) within [RayKernels/index.md] and [RayBCs/index.md#creating-a-new-ray] for creating [Rays](Ray.md) within [RayBCs/index.md].

### Unique Ray IDs

The `RayTracingStudy` requires internally that every [Ray.md] that is traced has a unique ID. This process can be troublesome when generating [Rays](Ray.md) across multiple threads and multiple processors.

To resolve this issue, you may obtain a unique ID for a [Ray.md] using `generateUniqueRayID()`. To reset the unique IDs back to their initial values, use `resetUniqueRayIDs()`.

### Side Normal Caching

There exists the need to obtain the outward normal for an element's side for many use cases of the [ray_tracing/index.md].

The `RayTracingStudy` can provide outward side normals for an element on the fly. It also caches the generated normal for future requests for the same side normal. This is accessed through the `getSideNormal()` method.
